"""Generates Kubernetes secrets based on a provided app name.

If the `templates` directory contains a secret called `stackspin-{app}-variables`, it
will check if that secret already exists in the cluster, and if not: generate
it. It does the same for an `stackspin-{app}-basic-auth` secret that will contain a
password as well as a htpasswd encoded version of it.

See https://open.greenhost.net/stackspin/stackspin/-/issues/891 for the
context why we use this script and not a helm chart to generate secrets.

usage: `python generate_secrets.py $appName`

As a special case, `python generate_secrets.py stackspin` will check that the
`stackspin-cluster-variables` secret exists and that its values do not contain
problematic characters.
"""

import base64
import crypt
import os
import secrets
import string
import sys

import jinja2
import yaml
from kubernetes import client, config
from kubernetes.client import api_client
from kubernetes.client.exceptions import ApiException
from kubernetes.utils import create_from_yaml
from kubernetes.utils.create_from_yaml import FailToCreateError

# This script gets called with an app name as argument. Most of them need an
# oauth client in Hydra, but some don't. This list contains the ones that
# don't.
APPS_WITHOUT_OAUTH = [
    "single-sign-on",
    "prometheus",
    "alertmanager",
]


def main():
    """Run everything."""
    # Add jinja filters we want to use
    env = jinja2.Environment(
        extensions=["jinja2_base64_filters.Base64Filters"])
    env.filters["generate_password"] = generate_password

    if len(sys.argv) < 2:
        print("Please provide an app name as an argument")
        sys.exit(1)
    app_name = sys.argv[1]

    if app_name == "stackspin":
        # This is a special case: we don't generate new secrets, but verify the
        # validity of the cluster variables (populated from .flux.env).
        verify_cluster_variables()
    else:
        # Create app variables secret
        create_variables_secret(
            app_name, f"stackspin-{app_name}-variables.yaml.jinja", env)
        # Create a secret that contains the oauth variables for Hydra Maester
        if app_name not in APPS_WITHOUT_OAUTH:
            create_variables_secret(
                app_name, "stackspin-oauth-variables.yaml.jinja", env)
        create_basic_auth_secret(app_name, env)


def verify_cluster_variables():
    data = get_kubernetes_secret_data("stackspin-cluster-variables", "flux-system")
    if data is None:
       raise Exception("Secret stackspin-cluster-variables was not found.")
    message = "In secret stackspin-cluster-variables, key {}, the character {}" \
        " was used which will probably lead to problems, so aborting." \
        " You can update the value by using `kubectl edit secret -n" \
        " flux-system stackspin-cluster-variables`."
    for key, value in data.items():
        decoded_value = base64.b64decode(value).decode("ascii")
        for character in ["\"", "$"]:
            if character in decoded_value:
                raise Exception(message.format(key, character))


def get_templates_dir():
    """Returns directory that contains the Jinja templates used to create app secrets."""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")


def create_variables_secret(app_name, variables_filename, env):
    """Checks if a variables secret for app_name already exists, generates it if necessary."""
    variables_filepath = os.path.join(get_templates_dir(), variables_filename)
    if os.path.exists(variables_filepath):
        # Check if k8s secret already exists, if not, generate it
        with open(variables_filepath, encoding="UTF-8") as template_file:
            lines = template_file.read()
            secret_name, secret_namespace = get_secret_metadata(lines)
            new_secret_dict = yaml.safe_load(
                env.from_string(lines, globals={"app": app_name}).render()
            )
            current_secret_data = get_kubernetes_secret_data(
                secret_name, secret_namespace
            )
            if current_secret_data is None:
                # Create new secret
                update_secret = False
            elif current_secret_data.keys() != new_secret_dict["data"].keys():
                # Update current secret with new keys
                update_secret = True
                print(
                    f"Secret {secret_name} in namespace {secret_namespace}"
                    " already exists. Merging..."
                )
                # Merge dicts. Values from current_secret_data take precedence
                new_secret_dict["data"] |= current_secret_data
            else:
                # Do Nothing
                print(
                    f"Secret {secret_name} in namespace {secret_namespace}"
                    " is already in a good state, doing nothing."
                )
                return
            print(
                f"Storing secret {secret_name} in namespace"
                f" {secret_namespace} in cluster."
            )
            store_kubernetes_secret(
                new_secret_dict, secret_namespace, update=update_secret
            )
    else:
        print(
            f"Template {variables_filename} does not exist, no action needed")


def create_basic_auth_secret(app_name, env):
    """Checks if a basic auth secret for app_name already exists, generates it if necessary."""
    basic_auth_filename = os.path.join(
        get_templates_dir(), f"stackspin-{app_name}-basic-auth.yaml.jinja"
    )
    if os.path.exists(basic_auth_filename):
        with open(basic_auth_filename, encoding="UTF-8") as template_file:
            lines = template_file.read()
            secret_name, secret_namespace = get_secret_metadata(lines)

            if get_kubernetes_secret_data(secret_name, secret_namespace) is None:
                basic_auth_username = "admin"
                basic_auth_password = generate_password(32)
                basic_auth_htpasswd = gen_htpasswd(
                    basic_auth_username, basic_auth_password
                )
                print(
                    f"Adding secret {secret_name} in namespace"
                    f" {secret_namespace} to cluster."
                )
                template = env.from_string(
                    lines,
                    globals={
                        "pass": basic_auth_password,
                        "htpasswd": basic_auth_htpasswd,
                    },
                )
                secret_dict = yaml.safe_load(template.render())
                store_kubernetes_secret(secret_dict, secret_namespace)
            else:
                print(
                    f"Secret {secret_name} in namespace {secret_namespace}"
                    " already exists. Not generating new secrets."
                )
    else:
        print(f"File {basic_auth_filename} does not exist, no action needed")


def get_secret_metadata(yaml_string):
    """Returns secret name and namespace from metadata field in a yaml string."""
    secret_dict = yaml.safe_load(yaml_string)
    secret_name = secret_dict["metadata"]["name"]
    # default namespace is flux-system, but other namespace can be
    # provided in secret metadata
    if "namespace" in secret_dict["metadata"]:
        secret_namespace = secret_dict["metadata"]["namespace"]
    else:
        secret_namespace = "flux-system"
    return secret_name, secret_namespace


def get_kubernetes_secret_data(secret_name, namespace):
    """Returns the contents of a kubernetes secret or None if the secret does not exist."""
    try:
        secret = API.read_namespaced_secret(secret_name, namespace).data
    except ApiException as ex:
        # 404 is expected when the optional secret does not exist.
        if ex.status != 404:
            raise ex
        return None
    return secret


def store_kubernetes_secret(secret_dict, namespace, update=False):
    """Stores either a new secret in the cluster, or updates an existing one."""
    api_client_instance = api_client.ApiClient()
    if update:
        verb = "updated"
        api_response = patch_kubernetes_secret(secret_dict, namespace)
    else:
        verb = "created"
        try:
            api_response = create_from_yaml(
                api_client_instance,
                yaml_objects=[secret_dict],
                namespace=namespace
            )
        except FailToCreateError as ex:
            print(f"Secret not {verb} because of exception {ex}")
            return
    print(f"Secret {verb} with api response: {api_response}")


def patch_kubernetes_secret(secret_dict, namespace):
    """Patches secret in the cluster with new data."""
    api_client_instance = api_client.ApiClient()
    api_instance = client.CoreV1Api(api_client_instance)
    name = secret_dict["metadata"]["name"]
    body = {}
    body["data"] = secret_dict["data"]
    return api_instance.patch_namespaced_secret(name, namespace, body)


def generate_password(length):
    """Generates a password of "length" characters."""
    length = int(length)
    password = "".join((secrets.choice(string.ascii_letters)
                        for i in range(length)))
    return password


def gen_htpasswd(user, password):
    """Generate htpasswd entry for user with password."""
    return f"{user}:{crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))}"


if __name__ == "__main__":
    config.load_kube_config()
    API = client.CoreV1Api()
    main()

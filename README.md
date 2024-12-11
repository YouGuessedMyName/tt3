# Python AMP adapter for Matrix/Synapse
In order to run the adapter properly, you need a Synapse server running on your local computer with at least four users:
* `admin` with password `admin`. (Needs to have administrator priviledges)
* `one` with password `one`
* `two` with password `two`
* `three` with password `three`

Then start the adapter by executing
```sh
python3 src/adapter/plugin_adapter.py -u {AMP_URL} -t {TOKEN} -n {NAME}
```
Once you connect to the adapter in AMP, you can configure two variables:
* `endpoint`: set this to the ip address of your Matrix server.
* `docker_container`: set this to the name of your docker container. This is used for restarting the server.

Then, upload the `model.aml` to AMP and set it as your project root model file. You should now be able to run the model.
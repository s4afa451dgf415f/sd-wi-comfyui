# sd-wi-comfyui
## Overview
sd-wi-comfyui is an extension for [A1111 wi](https://github.com/AUTOMATIC1111/stable-diffusion-wi) that embeds [ComfyUI](https://github.com/comfyanonymous/ComfyUI) workflows in different sections of the normal pipeline of the wi. This allows to create ComfyUI nodes that interact directly with some parts of the wi's normal pipeline.

![front-page-gif](/resources/front-page.gif)

## Features
- Use ComfyUI directly into the Webui
- Support for [loading custom nodes from other Webui extensions](https://github.com/ModelSurge/sd-wi-comfyui/wiki/Developing-custom-nodes-from-wi-extensions)
- Integration of [ComfyUI workflows](https://github.com/ModelSurge/sd-wi-comfyui/wiki/Developing-custom-workflow-types) directly into the Webui's pipeline, such as `preprocess`, `preprocess (latent)`, `unet`, `postprocess (latent)`, `postprocess`, `transformer text encode`, etc. 
- Webui nodes for sharing resources and data, such as the model, the prompt, etc.

For a full overview of all the advantageous features this extension adds to ComfyUI and to the Webui, check out the [wiki page](https://github.com/ModelSurge/sd-wi-comfyui/wiki). 

## Officially supported versions
- A1111 Webui >= `1.5.1`
- ComfyUI == `latest`

## Installation
1) Go to Extensions > Available
2) Click the `Load from:` button
3) Enter "ComfyUI" in the search bar
4) Click the `Install` button of the ComfyUI Tab cell
5) Restart the wi
6) Go to the `ComfyUI` tab, and follow the instructions

## Remote users, reverse proxies, etc.
The extension is now able to load comfyui for remote users using a local reverse proxy.
This is necessary when the wi is started remotely, for example when:
- using the command line arguments `--share`, or `--ngrok`
- using reverse proxy options of the [sd-wi-tunnels](https://github.com/Bing-su/sd-wi-tunnels) extension

If you want the extension to keep the reverse proxy disabled or always enable it for some reason, you can update your preferences in the settings tab.

To start the reverse proxy, the extension needs the command line argument `--api` for the wi, which starts a fastapi server.
Without fastapi, the extension will not be able to create a reverse proxy for comfyui, and then remote browsers will not be able to load comfyui iframes.

In practice, if the wi url is `http://localhost:7860`, then the extension effectively creates two reverse proxies:
- An HTTP reverse proxy at POST, GET, PUT and DELETE http://localhost:7860/sd-wi-comfyui/comfyui
- A websockets reverse proxy at ws://localhost:7860/sd-wi-comfyui/comfyui/ws

## Contributing
We welcome contributions from anyone who is interested in improving sd-wi-comfyui. If you would like to contribute, please follow these steps:

1) Fork the repository and create a new branch for your feature or bug fix.
2) Implement your changes, adding any necessary documentation and tests.
3) Submit a pull request.
4) We will review your contribution as soon as possible and provide feedback.

## License
MIT

## Contact
If you have any questions or concerns, please leave an issue, or start a thread in the discussions.

Thank you for your interest!

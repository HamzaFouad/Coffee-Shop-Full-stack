# Coffee Shop Backend

## Getting Started

### Frontend

#### Installing Node and NPM

This project depends on Nodejs and Node Package Manager (NPM). Before continuing, you must download and install Node (the download includes NPM) from [https://nodejs.com/en/download](https://nodejs.org/en/download/).

#### Installing Ionic Cli

The Ionic Command Line Interface is required to serve and build the frontend. Instructions for installing the CLI  is in the [Ionic Framework Docs](https://ionicframework.com/docs/installation/cli).

#### Installing project dependencies

This project uses NPM to manage software dependencies. NPM Relies on the package.json file located in the `frontend` directory of this repository.
After cloning, open your terminal and run(Inside `Frontend` folder):

```bash
npm install
```

>_tip_: **npm i** is shorthand for **npm install**

### Backend

#### Installing Dependencies

Create a virtualenv and activate it

```bash
python3 -m virtualenv coffee-shop-venv
source coffee-shop-venv/bin/activate
```

then inside `backend` directory run:

```bash
pip install -r requirements.txt
```

## Running the server

### frontend

Inside `fontend` directory run:

```bash
ionic serve
```

### backend

From within the `./src` directory first ensure you are working using the virtual environment you created.

Then run the following command:

```bash
chmod +x run_flaskapp.sh
./run_flaskapp.sh
```

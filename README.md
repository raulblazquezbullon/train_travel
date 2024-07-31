# Train travel

I'm tired of looking train travels in Renfe, OUIGO and Iryo, so let's get the best possible result using Python.

## How to

First, you have to install the requirements (we strongly recommend `virtualenv`):

```bash
pip install -r requirements.txt
```

You must install Docker Desktop if you want to test it, so go to [Docker](https://www.docker.com/products/docker-desktop/) and install it like any other application (if you are on Windows, you may have to activate the Hyper-V thing).

Then, you have to pull the image from `selenium` project:

```bash
docker pull selenium/standalone-chrome
```

Build the image in your local computer:

```bash
docker build -t train-travel-app .
```

Finally, run the container:

```bash
docker run -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-chrome:latest
```

You are ready to execute the code:

```bash
python3 train_travel/scraper/renfe_scraper.py
```

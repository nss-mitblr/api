# NSS MIT-BLR Volunteer App

> ⚠️ **Notice:** This repository currently acts as a proof-of-concept, not an MVP or a production-ready system. For further information on the project's status, please refer to [History](#history).

## Contributors

- Hari Keshav Rajesh [(GitHub)](https://github.com/Hari-Keshav-Rajesh) [(LinkedIn)](https://www.linkedin.com/in/hari-keshav-rajesh-b25945300/)
- Raghav Gupta [(GitHub)](https://github.com/Alphaspiderman) [(LinkedIn)](https://www.linkedin.com/in/raghav-gupta-ind/)

## Accompanying Repositories

The NSS MIT-BLR Volunteer App project is divided into two repositories, the API (you are here) and the mobile application. The mobile application repository can be found at [nss-mitblr/app](https://github.com/nss-mitblr/app)

## History

On 13th August, 2024, the team commenced work on an application for the volunteers of NSS MIT-BLR in order to centralize their event contribution and resource management. This application was created with the aim to streamline administrative workflows and reduce the time spent in shift and volunteer hour calculation.

The project was archived on 20th February, 2025 after an elongated period of inactivity from the Core Committee, and inability to provide the hosting resources for the API that accompanies the application.

While we were unable to implement this project successfully, this repository remains public to provide other such endeavours with a headstart.

## Configuration

All core config values of the API exist as enviroment variables, a sample ENV file can be found at [`.env-example`](.env-example).


## Development

1. Install the dependency manager:

   ```bash
   pip install poetry
   ```

2. Install the dependencies:

   ```bash
   poetry install
   ```

3. Configure the environment variables:

   ```bash
   cp .env-example .env
   ```

4. Generate an RSA keypair:

   ```bash
   openssl genrsa -out private.pem 2048
   openssl rsa -in private.pem -pubout -out public.pem
   ```

5. Run the development server:

   ```bash
    poetry run task server
    ```

The project is now ready for development!

# Facebook Shop MCP Agent

An AI-powered agent built on the Model Context Protocol (MCP) that helps businesses sell products through Facebook Shop.

## Overview

This agent integrates with Facebook Shop to streamline and automate the product selling process. By leveraging MCP, the agent can interact with Facebook's commerce platform to manage listings, respond to customer inquiries, and drive sales — all with minimal manual effort.

## Features

- **Product Management** — List, update, and remove products from your Facebook Shop
- **Sales Assistance** — AI-guided support for closing sales and engaging potential buyers
- **Inventory Sync** — Keep your product catalog up to date automatically
- **Customer Interaction** — Handle common buyer questions and inquiries
- **MCP Integration** — Built on the Model Context Protocol for flexible AI tooling and extensibility

## Getting Started

### Prerequisites

- A Facebook Business account with Shop enabled
- Node.js (v18 or later) or Python (3.10 or later), depending on your setup
- Facebook Graph API credentials

### Installation

```bash
git clone https://github.com/rdinesh207/facebook-shop-agent.git
cd facebook-shop-agent
npm install   # or pip install -r requirements.txt
```

### Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Set the following variables in `.env`:

```
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id
```

### Running the Agent

```bash
npm start   # or python main.py
```

## Usage

Once running, the agent connects to your Facebook Shop and begins managing product listings and assisting with sales. You can interact with it through the MCP interface or configure it to run autonomously.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT

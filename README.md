# ToDoBee Slack App

**ToDoBee** is a lightweight Slack integration that helps you manage your to-do list directly from Slack threads. By reacting with the `:todobee:` emoji, the app will collect the message link and notify you daily with a checklist of your saved threads.

## Features

- Add Slack thread messages to your to-do list by simply reacting with `:todobee:`.
- Automatically gathers links to the threads you've marked.
- Sends you a daily reminder at **9 AM UTC** listing all your to-dos.
- Supports both public and private Slack channels.

---

## Prerequisites

Before running the app, ensure the following:

- **Slack Workspace Setup**
  - Add your Slack workspace details in the `manage_data` file.
  
- **Slack Bot Token**
  - Generate a bot token for your Slack app and update it in the `app` file.
  - [How to create a Slack bot token](https://api.slack.com/authentication/token-types#bot)

---

## Deployment

The application is containerized using Docker and deployed on **AWS Lambda** using the **latest Docker image from Amazon ECR**.

- AWS Lambda function is configured to use the latest image version.
- An **AWS API Gateway** is integrated to expose a public endpoint.
- This endpoint is registered with your Slack app to receive and process Slack events.

---

## Installation Guide

1. **Create a Slack App**
   - Go to [Slack API: Your Apps](https://api.slack.com/apps) and create a new app in your workspace.

2. **Create and Add Bot Token**
   - Add the generated bot token in the `app` file.

3. **Set the Request URL**
   - Use the API Gateway endpoint as the request URL in the **Event Subscriptions** section of your Slack app.

4. **Assign Required Scopes**
   - The app needs the following OAuth scopes:
     - `channels:history`
     - `groups:history`
     - `chat:write`
     - `users:read`
     - `reactions:read`

5. **Install the App**
   - Install the app on your Slack workspace.
   - Add the bot to the channels where you want to use it.

---

## Usage

To test the app:

1. Add the `:todobee:` emoji reaction to any message in a thread.
2. The app will capture the message link and store it.
3. At **9 AM UTC**, you'll receive a reminder listing all your active to-do thread links in a checklist format.

---

## Development Notes

- All Slack message data is stored and processed as links only. No message content is stored.
- Users only see their own to-do lists.
- Future versions may include interactive buttons for marking tasks as done or snoozing reminders.

---

## License

This project is currently not open-source. For internal use only.

---

## Support

For bugs, suggestions, or feedback, please open an issue or contact the maintainer.





# meetup-facebook-bot
FIXME: write the description

# Setup
1. Register [Facebook](https://developers.facebook.com/docs/messenger-platform/guides/setup) and [Heroku](https://dashboard.heroku.com) apps. 
2. Set environment variables: `VERIFY_TOKEN` is a Facebook verify token and `ACCESS_TOKEN` is a Facebook access token. Both were created during the first step.
3. Set environment variable: `app_id`: To check your app_id: firstly login to https://developers.facebook.com/apps, then choose your app and copy APP_ID from top left corner of that page.
4. Set environment variable: `page_id`: Then navigate to your page, click on information, scroll to the bottom of the page and copy PAGE_ID.
5. Clone the repository.
6. [Set Heroku as a remote repository](https://stackoverflow.com/questions/5129598/how-to-link-a-folder-with-an-existing-heroku-app) and push the source to `heroku master`, effectively deploying the app.

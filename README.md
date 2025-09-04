# Farm YouTube engagement using live thumbnails

Growth strategy: users who comment on your video appear on your thumbnail in semi-real-time.

TODO: GIF here (mix in capcut, screen record, convert to GIF keep mp4 preview JIC)

<details>
<summary>1. Any prerequisites?</summary>

### Your video ID

![Find your YouTube video ID](./README/find-your-youtube-video-id.jpg)

### Your thumbnail
To keep things simple, the sample thumbnail has 5 slots for PFPs with positions known ahead-of-time (hard-coded as a [constant](./app/constants.py)). This can easily be changed to allow, pasting hundreds of small PFPs covering the entire thumbnail.

![base thumbnail](./app/assets/base_thumbnail.jpeg) 

### Your YouTube API access
Using an API key is simple for reads (listing comments) but OAuth is required for writes (setting thumbnails). Unfortunately, there is no silver-bullet (permanent auth) for backend to backend (this web API to YouTube's API). You will need to BYO Refresh Token (long-lived) to ensure the web API has continuous access. A script is provided to trigger an interactive login (login as the channel owner) to obtain a refresh token.

Lifespan of Google's Refresh Token? As of writing, they appear to be `~600k seconds ≈ 7 days`. This is plenty of time for this project's purpose. Recommend storing in a secrets vault (e.g., Azure Key Vault) and restart the web API/create an operational endpoint to hot reload the YouTube client with the new Refresh Token.

1. Create [.env](./.env) to populate in the subsequent steps
   ```shell
   cp .env.example .env
   ```
2. Get your **Client ID** and **Client Secret** by generating your Google OAuth Client [here](https://console.cloud.google.com/apis/credentials) (choose Desktop to avoid specifying origins and redirect URLs etc)  
   ![How to generate YouTube API key step 1](./README/how-to-create-youtube-oauth-client.jpg)
3. Before the next step, you may need to add your account (channel owner account) as a test user if your app is unpublished  
   ![How to add your account as a test user](./README/how-to-set-test-users.jpg)
4. To get the **Refresh Token**, run the script (will launch your browser) and login
   ```shell
   chmod +x script_to_obtain_refresh_token.py
   ./script_to_obtain_refresh_token.py
   ```
5. You now have the **Client ID**, **Client Secret**, add **Refresh Token**, add them to [.env](./.env)
6. That's it for environment variables!
7. If you are a new channel, YouTube may block you from setting custom thumbnails. To fix this, try to change the thumbnail via YouTube's frontend and Google will ask you to verify.

</details>

<details>
<summary>2. How do I use it?</summary>

- Assumes you're using asdf (last using Python 3.13.7)
- Assumes you haven't used 100% of your YouTube API daily quota
- How to start the web API? Run in [root](.)
  ```shell
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  fastapi dev app
  ```
- How to test the web API? See [app.http](app.http) then use cURL or [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
- Generated (test and official) thumbnails will go [here](./generated_thumbnail/)

</details>

<details>
<summary>3. FAQ</summary>

### _"What are the next steps to deploy?"_
- Run the web API on a VPS, example: [Digital Ocean Droplet @ $4/month](https://www.digitalocean.com/pricing)
- Run a CRON job on the VPS to trigger endpoint every X minutes, example:
  ```shell
  */X * * * * curl -s -H "Accept: application/json" "http://localhost:8000/farm-engagement?limit={{num_of_top_comments}}&video_id={{video_id}}" > /dev/null 2>&1
  ```

### _"Any improvements?"_
- You can add funnels to only process users who have liked/commented/subscribed - maxxing interactions.
- Persist the current progress in an external DB to avoid data loss (users processed so far, cursor position to paste the next PFP, the latest thumbnail, etc).
- More dynamic behaviour, for example: reduce the image quality if YouTube's >2MB limit, scale down the update thumbnail cadence based on remaining quota per day, fetch comments paginated (costs more reads), etc.
- YouTube's _order by relevance_ query param may not return comments immediately for a brand new video, fallback to retrying fetching comments with _order by time_ for resiliency.
- Add caching for previously seen/downloaded PFPs.
- Add logging.

### _"So this gets the top comments?"_
YouTube's _order by relevance_ query param when fetching the top comments is not the same algo as the one you see on YouTube's frontend - they are similar (enough to get the job done) but not 1:1.

### _"Why not just fetch all comments so we have more control?"_
Yes this would guarentee we always rank comments with 100% accuracy and allows us to promise, for example, "top 3 comments with the most likes get chosen...". This is a quota issue: use more quota to get all comments paginated VS get a fixed set of comments to preserve quota for near-real-time thumbnail updates. For this demo, prioritize simplicity: get the top 100 comments (first page) based on Google's relevance ordering.

</details>

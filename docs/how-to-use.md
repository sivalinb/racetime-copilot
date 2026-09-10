# How to use RaceTime Copilot

**Paste a race video link, choose the part you missed, and ask a question.** RaceTime aims to give you a short recap with timestamps you can check.

## 1. Add your video

1. Open the app and select **Video workspace** if a workspace switch is shown.
2. Choose **Create account** the first time, then sign in.
3. Open **Videos**, give the video a title, and paste a **public YouTube video or livestream URL**.
4. Click **Save video**. You can also upload an MP4, MOV or WebM instead of pasting a link.

Saving a link does not start analysis. Use the next steps to choose what to watch.

## 2. Ask about a recorded video

Open **Ask / inspect**, choose your saved video, and select **Ask the agent**.

For example, to catch up from minute 10 to minute 15:

| Field | Enter |
|---|---|
| Start / current live elapsed time | `10:00` |
| End | `15:00` |
| Spoiler cutoff | `15:00` |
| Question | `What happened between 10:00 and 15:00? Summarize the key moments.` |

Click **Queue job**, then open **Jobs / results** and click **Refresh jobs** to see progress.

Use `MM:SS` or `HH:MM:SS`, measured from the start of the video. For example, `01:10:00` means one hour and ten minutes. Set the spoiler cutoff to the End time to keep later evidence out.

**Set the Start and End fields even if you mention times in your question.** The app currently uses those fields to choose the interval; typing times in the question does not update them. Match the question to the fields.

## 3. Questions you can try

Use these with the same `10:00`–`15:00` interval, or change both the fields and the times in the question:

- “What happened between 10:00 and 15:00? Give me a quick catch-up.”
- “Which important moments were visible or mentioned between 10:00 and 15:00? Include timestamps.”
- “Was bib 42 shown or mentioned in this interval? Say if there is not enough evidence.”
- “What did the commentators say about the leaders during this interval?”
- “What happened at the aid station? Separate what was visible from what was said.”
- “Were there conflicting reports in this interval? Explain both without guessing which is correct.”

A name, bib number or race position must be visible or mentioned in the evidence. Asking about one does not guarantee it was captured.

## 4. Ask about a livestream

1. Save a **currently live, public YouTube URL** under Videos.
2. Under **Ask / inspect**, choose **Capture a live stream**.
3. Enter the broadcast's current elapsed time as Start. For example, use `01:00:00` to `01:15:00`, with cutoff `01:15:00`, to capture the next 15 minutes.
4. Click **Queue job**. The app records from the current live edge and processes completed pieces in the background.
5. Refresh **Jobs / results**. Once pieces have been processed, choose **Ask the agent** for that saved stream.
6. Select **Use the last 15 minutes of processed live coverage**, then ask: “What happened in the last 15 minutes of available footage?” Or enter a specific captured interval yourself.

The checkbox uses the latest processed footage, which may lag behind the live broadcast. Capture is limited to 15 minutes per session. Footage from before capture started is not automatically available. Keep the local app launcher running while it works; a closed browser tab does not stop the worker.

## 5. What you should see

The job moves from **queued** to **running**, then usually **awaiting_review** when a recap is ready. Expect:

- A short answer with timestamp links for YouTube, or playback buttons for uploaded video.
- Notices about missing footage, unclear evidence or other limitations.
- An explanation when there is not enough evidence, or an error when the video cannot be processed.
- **Approved** and **Rejected** buttons for your review, plus **Export result** to save the answer and evidence.

**Illustrative output only — these are fictional race events:**

> Between 10:00 and 15:00, a runner arrived at an aid station [10:24]. The commentator reported a smaller gap between the leaders [12:08]. The footage did not establish an official race position.

The actual answer depends on your footage. Timestamps help you verify it; they do not guarantee the AI is correct. Check the source before approving. A reviewed recap is saved as **completed**, with your approval or rejection recorded.

## 6. What happens in the background

1. **Check your request.** The app checks the link, time range and account limits.
2. **Save the job.** A background worker picks it up, so you can keep using the app.
3. **Look for existing evidence.** It searches previously analyzed observations inside your chosen interval.
4. **Inspect when needed.** For a new recorded interval, Gemini examines the requested footage and creates timestamped notes. For live video, the capture job creates notes from completed segments.
5. **Find useful notes.** It selects observations relevant to your question and excludes those outside the time and cutoff rules.
6. **Choose the next step.** The agent can inspect again when permitted, summarize, or ask for clarification. Limits prevent it from looping indefinitely.
7. **Write and check the recap.** Gemini writes an answer linked to observations. A separate AI check looks for unsupported statements. If generation fails, the app can show labelled extracts instead.
8. **Wait for your review.** The app saves the recap, evidence and activity trail. You check the timestamps, then approve or reject. This review can resume after a restart.

## Current demo limits

Small MP4 uploads under 12 MB have passed an end-to-end integration check. The shared YouTube race URL and larger-file processing encountered provider errors during testing. If a URL fails, try a short MP4 or switch to the key-free **Evidence demo** with the fictional Canyon Relay race. Real-race accuracy still needs independent review. The live workflow is implemented but its active-stream test is deferred.

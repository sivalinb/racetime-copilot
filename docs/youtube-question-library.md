# 100 useful YouTube questions and scenarios

**A practical prompt library for RaceTime Copilot.** The first 20 ideas target the successfully analyzed 05:00–08:00 interval of [this race discussion](https://www.youtube.com/watch?v=S_9wb3g7jtY&t=300). The other 80 can be used with suitable race broadcasts, interviews, briefings and training videos. They do not imply that this particular video contains those events.

**Status: 100 authored suggestions, not 100 passed tests.** Only the earlier general recap request has been run. Each expected response below describes useful behavior, not a verified answer or golden label.

## How to use the library

1. Save a public YouTube URL in **Video workspace → Videos**.
2. Choose **Ask / inspect → Ask the agent** and set **Start**, **End** and **Spoiler cutoff**. For questions 1–20, use `05:00`, `08:00`, `08:00`.
3. Copy one question. Replace `[RUNNER]`, `[BIB]`, `[TOPIC]`, `[START]` and similar placeholders. For questions 21–100, choose a source and interval likely to contain the subject.
4. Queue the job, review the timestamped evidence and then approve or reject. Content absent from the interval should produce an explicit limitation, not a guess.

Times in the question do not set the app fields. RaceTime currently produces short cited narratives; complex tables, exact counts, exhaustive frame searches and precise speaker attribution are not guaranteed. These prompts can guide a recap, but format and specialized extraction quality still need testing.

A timestamp shortlist does not create clips. A draft update is not automatically sent. Requests use the selected video evidence; they do not fetch current race results, official rules, weather forecasts, maps or private live-chat history. Live questions need previously captured and processed coverage.

## Best five to try first

- **YT-001:** a useful catch-up after stepping away.
- **YT-014:** registration figures matched to the correct races.
- **YT-016:** distinguish a confirmed announcement from a possible lottery.
- **YT-021:** follow a runner using explicit identifying evidence in suitable footage.
- **YT-100:** a practical source-review checklist before approving a recap.

## Catch up on this race briefing

*Use the shared video at 05:00–08:00.*

### YT-001 — Returning after a meeting

> What happened between 05:00 and 08:00? Give me the three most useful updates.

**Useful response:** A concise recap of the main discussion with supporting timestamps.

### YT-002 — Only 30 seconds to read

> Give me a 30-second catch-up for 05:00–08:00, with a timestamp for each main point.

**Useful response:** A short, cited catch-up rather than a transcript.

### YT-003 — Choose what to replay

> Which two moments in 05:00–08:00 are most worth replaying to understand the race updates? Explain why.

**Useful response:** Two source moments selected for informational value, with reasons.

### YT-004 — Find the topic transitions

> Between 05:00 and 08:00, when does the speaker change topics? Give me a short topic timeline.

**Useful response:** Approximate topic boundaries supported by observations.

### YT-005 — Skip the interruptions

> Summarize 05:00–08:00 while leaving out greetings, pauses and nonessential interruptions.

**Useful response:** Race information retained; incidental actions omitted.

### YT-006 — Distinguish scenery from discussion

> In 05:00–08:00, which course details are spoken about and which are actually shown?

**Useful response:** Commentary separated from visible course evidence; no invented scenery.

### YT-007 — New viewer orientation

> Explain the races mentioned in 05:00–08:00 to someone new to this event, using only what the speaker says.

**Useful response:** A brief orientation that marks unexplained names or concepts.

### YT-008 — Separate certainty from possibilities

> Which statements in 05:00–08:00 are presented as updates, and which are speculation or future possibilities?

**Useful response:** Speaker assertions distinguished from tentative statements.

### YT-009 — Prepare follow-up questions

> After hearing 05:00–08:00, what three useful race questions remain unanswered by this segment?

**Useful response:** Questions derived from missing context, clearly not answered facts.

### YT-010 — Find a useful bookmark

> Where in 05:00–08:00 should I jump to hear the registration discussion?

**Useful response:** Timestamp links near the relevant discussion, with approximate timing disclosed.

## Make this briefing useful to a runner

*Use the shared video at 05:00–08:00.*

### YT-011 — Understand the Mingus route

> What landmarks does the speaker mention for Mingus Traverse 80 in 05:00–08:00? Preserve the spoken order.

**Useful response:** Landmarks attributed to the speaker; no added route geography.

### YT-012 — Check the stated finish

> What finish location is mentioned for Mingus Traverse in 05:00–08:00? Show the evidence.

**Useful response:** A cited location if supported, with no claim of current official guidance.

### YT-013 — Understand shared course sections

> How does the speaker describe Bradshaw Brute’s relationship to the 250 course in 05:00–08:00?

**Useful response:** The stated route relationship without inferring a complete course map.

### YT-014 — Collect registration numbers

> List the registration figures mentioned in 05:00–08:00 and match each number to its race.

**Useful response:** A concise race-to-number mapping with timestamps and attribution.

### YT-015 — Keep waitlist and entry separate

> In 05:00–08:00, which Sedona Canyons figures refer to registered runners and which refer to the waitlist?

**Useful response:** Separate labels that avoid adding waitlisted people to confirmed starters.

### YT-016 — Assess a possible lottery

> Does the speaker announce a confirmed lottery or discuss it as a possibility in 05:00–08:00?

**Useful response:** The degree of certainty in the source, not a predicted entry policy.

### YT-017 — Compare two race updates

> Compare what the speaker says about Bradshaw Brute and Mingus Traverse in 05:00–08:00.

**Useful response:** Only dimensions covered in the segment; missing details stated explicitly.

### YT-018 — Find the Cocodona update

> What is the Cocodona 250 update in 05:00–08:00, and where can I replay it?

**Useful response:** A brief attributed update with the relevant timestamp.

### YT-019 — Avoid treating old figures as current

> What registration information is stated in 05:00–08:00, and does this interval establish when those figures were current?

**Useful response:** Numbers attributed to the recording; date uncertainty preserved.

### YT-020 — Prepare a registration checklist

> Based on 05:00–08:00, what should a prospective entrant verify with the organizer before making plans?

**Useful response:** A short checklist of open questions; no invented deadlines or availability.

## Follow an athlete without guessing

*Use a suitable source and selected time interval; the subject may be absent.*

### YT-021 — Check a named runner

> Was [RUNNER] explicitly named or shown with a readable identifier between [START] and [END]?

**Useful response:** Positive identification only from explicit evidence; otherwise uncertainty.

### YT-022 — Find a bib sighting

> Was bib [BIB] visible or mentioned in this interval? Give the supported moments.

**Useful response:** Cited sightings or an evidence-limited no-confirmed-sighting response.

### YT-023 — Catch up with a favorite

> Summarize only updates explicitly about [RUNNER] in this interval.

**Useful response:** A focused recap that excludes unrelated runners and inferred identity.

### YT-024 — Tell a mention from an appearance

> For [RUNNER], separate commentary mentions from visually confirmed appearances.

**Useful response:** Evidence type distinguished for each supported moment.

### YT-025 — Locate an aid-station arrival

> Is there evidence that [RUNNER] arrived at [AID STATION] during this interval?

**Useful response:** A supported arrival moment, or an explicit inability to confirm.

### YT-026 — Locate an aid-station departure

> Is [RUNNER] explicitly shown or described leaving [AID STATION] in this interval?

**Useful response:** A cited departure observation without estimating unsupported timing.

### YT-027 — Follow changes in the report

> What different updates about [RUNNER] occur in this interval, in time order?

**Useful response:** A bounded sequence; no events imported from elsewhere in the race.

### YT-028 — Check a drop-out claim

> Does this segment explicitly report that [RUNNER] withdrew, or is that only speculation?

**Useful response:** Attributed statements with uncertainty; no inference from absence.

### YT-029 — Understand a delayed update

> Does the commentary say an update about [RUNNER] is delayed or from earlier?

**Useful response:** Any stated delay retained; broadcast time distinguished from event time.

### YT-030 — Avoid false reassurance

> What can this interval confirm about [RUNNER], and what can it not establish?

**Useful response:** Evidence-supported status only; no safety assurance from lack of coverage.

## Help crews and families stay informed

*Use a suitable source and selected time interval; the subject may be absent.*

### YT-031 — Brief the next crew shift

> Give me a short crew handoff from this interval: confirmed updates, stated needs and open questions.

**Useful response:** A draft handoff linked to evidence; missing operational information marked.

### YT-032 — Locate an explicit request

> Did [RUNNER] or their crew explicitly ask for supplies or assistance in this interval?

**Useful response:** Only requests actually captured; no inferred need or medical diagnosis.

### YT-033 — Catch an organizer message

> What announcements in this interval are relevant to crews or supporters?

**Useful response:** An attributed summary of announcements, with timestamps.

### YT-034 — Verify meeting instructions

> Does this interval state where crews should meet runners? Quote only a short relevant phrase or paraphrase it.

**Useful response:** Source instructions with location/time ambiguity preserved.

### YT-035 — Check an access restriction

> Were crew-access restrictions or closed aid stations announced in this interval?

**Useful response:** Only announced restrictions; no claim that the video is current authority.

### YT-036 — Spot a gear discussion

> Which gear items are explicitly discussed or clearly visible during [RUNNER]’s stop?

**Useful response:** Observed items distinguished from assumptions about intended use.

### YT-037 — Understand an extended stop

> What is actually said or shown during this stop? Is a reason for the delay explicitly given?

**Useful response:** A descriptive recap without diagnosing fatigue, injury or motivation.

### YT-038 — Explain the broadcast to family

> Explain this interval in plain language for a family member unfamiliar with ultrarunning.

**Useful response:** A short accessible explanation grounded in the segment.

### YT-039 — Prepare a family update draft

> Draft a brief family update from confirmed information in this interval and flag anything uncertain.

**Useful response:** A draft for user review; nothing automatically sent.

### YT-040 — Find what to verify before driving

> What information is missing from this interval that my crew should verify before changing its travel plan?

**Useful response:** Open questions about location, timing and access; no inferred travel advice.

## Understand race developments and tactics

*Use a suitable source and selected time interval; the subject may be absent.*

### YT-041 — Check a lead-change report

> Was a lead change explicitly shown or reported in this interval? What is the evidence?

**Useful response:** Visual and commentary claims separated; no inferred official standing.

### YT-042 — Unpack a gap update

> What gaps between runners are explicitly reported, and at which broadcast moments?

**Useful response:** Reported gaps with units, identities and timestamps when available.

### YT-043 — Resolve conflicting gaps

> Do any reported gap figures disagree in this interval? Present both and explain the missing context.

**Useful response:** Both claims retained; no invented reconciliation.

### YT-044 — Separate position from camera order

> Does this interval establish race positions, or merely show runners in a particular camera order?

**Useful response:** No ranking inferred from edit or appearance order.

### YT-045 — Hear the athlete’s own strategy

> What strategy does [RUNNER] explicitly describe in this interval?

**Useful response:** Statements attributed to the athlete rather than inferred intent.

### YT-046 — Separate analyst opinion

> Which tactical explanations come from commentators, and which come directly from athletes?

**Useful response:** Attribution and opinion/fact distinction.

### YT-047 — Understand a visible change

> What changes in movement or equipment are clearly observed in this interval, without inferring why?

**Useful response:** Descriptive observations; no diagnosis or unsupported causal story.

### YT-048 — Find the central race storyline

> What is the main competitive storyline discussed in this interval, and what evidence supports it?

**Useful response:** A bounded synthesis that includes uncertainty and conflicting evidence.

### YT-049 — Distinguish split times from elapsed times

> Which numbers in this interval are described as splits, elapsed times or time gaps?

**Useful response:** Numbers labeled by the source; ambiguity left unresolved.

### YT-050 — Ask about pace responsibly

> Does this interval provide explicit pace or speed information? Report it without calculating from incomplete footage.

**Useful response:** Only supported numerical claims, or a clear absence of sufficient evidence.

## Understand the course and event logistics

*Use a suitable source and selected time interval; the subject may be absent.*

### YT-051 — Map the spoken route sequence

> Which course locations are mentioned, and in what stated order?

**Useful response:** A textual sequence; no fabricated map or inferred connections.

### YT-052 — Identify terrain discussion

> What terrain is described in this interval, and what terrain is actually visible?

**Useful response:** Spoken descriptions separated from visual observations.

### YT-053 — Check a route-change announcement

> Was a course change announced? Summarize the stated change and who announced it.

**Useful response:** A cited historical announcement, not a verified current navigation instruction.

### YT-054 — Catch a cutoff announcement

> What cutoff times or deadlines are explicitly stated, including any timezone or event-time context?

**Useful response:** Exact supported context; missing date/timezone flagged.

### YT-055 — Understand aid-station services

> Which services at [AID STATION] are explicitly mentioned in this interval?

**Useful response:** Stated services only; no assumptions about availability elsewhere.

### YT-056 — Check required-gear discussion

> What mandatory gear requirements are stated, and does the speaker identify an official rule source?

**Useful response:** Requirements attributed to the recording, with authority limits.

### YT-057 — Hear weather-related announcements

> What weather conditions or weather-related event changes are actually reported in this interval?

**Useful response:** Reported conditions/actions; no fresh forecast or safety conclusion.

### YT-058 — Extract start-wave information

> What starting times or wave assignments are announced in this interval?

**Useful response:** A concise supported mapping with unresolved identity/time context marked.

### YT-059 — Understand transport instructions

> What shuttle, parking or transport instructions are stated for runners and crews?

**Useful response:** A source-linked historical summary for verification before use.

### YT-060 — Make a planning follow-up list

> Which course or logistics details in this interval are ambiguous enough that I should check the official event guide?

**Useful response:** Specific unanswered questions tied to the discussion.

## Review the broadcast and find replay moments

*Use a suitable source and selected time interval; the subject may be absent.*

### YT-061 — Make a manual highlight shortlist

> Suggest up to three replay moments from this interval, with timestamps and why each matters.

**Useful response:** Timestamp recommendations; no claim that video clips were created.

### YT-062 — Find an interview topic

> Where does the interview discuss [TOPIC] in this interval? Summarize that part.

**Useful response:** Relevant approximate timestamp and grounded topic summary.

### YT-063 — Separate interview from race coverage

> Which parts of this interval are interviews, studio discussion or visible race activity?

**Useful response:** Only distinctions supported by the available observations.

### YT-064 — Find a correction on air

> Does anyone correct an earlier statement during this interval? State the original claim and correction.

**Useful response:** Both attributed claims and their order, if captured.

### YT-065 — Recover an audience answer

> Which audience questions are explicitly answered in this interval, and what answers are given?

**Useful response:** Visible/audible questions and answers; no access to unseen live chat.

### YT-066 — Review sponsor mentions

> Which sponsors are explicitly mentioned or clearly identified in this interval?

**Useful response:** A non-exhaustive observed list; no exact exposure-time or logo-detection claim.

### YT-067 — Choose a teaser without later results

> Write a short teaser for this interval that reveals nothing beyond the selected cutoff.

**Useful response:** A cited draft based only on selected evidence; no automatic posting.

### YT-068 — Find a human-interest moment

> Which moment in this interval best illustrates something an athlete actually says about their experience?

**Useful response:** A source-grounded example without invented feelings or backstory.

### YT-069 — Review missing camera context

> What important parts of the commentator’s story are not visually established by this interval?

**Useful response:** Specific evidence gaps, without pretending to inspect unseen footage.

### YT-070 — Locate a possible coverage interruption

> Do the observations show or mention a broadcast interruption? Identify it without guessing its technical cause.

**Useful response:** Supported interruption evidence; no exhaustive frame-level outage measurement.

## Learn from briefings, interviews and demos

*Use a suitable source and selected time interval; the subject may be absent.*

### YT-071 — Understand unfamiliar terminology

> Explain [TERM] as it is used in this interval; say if the speaker does not define it.

**Useful response:** Contextual explanation limited to source evidence.

### YT-072 — Recover a missed explanation

> What explanation did I miss between [START] and [END]? Give the key steps.

**Useful response:** A short ordered recap of the stated explanation.

### YT-073 — Separate advice from anecdote

> Which parts of this interview are personal experience and which are presented as general advice?

**Useful response:** Clear attribution and no assumption that anecdote proves a general rule.

### YT-074 — Collect the athlete’s lessons

> What lessons does the athlete explicitly say they learned?

**Useful response:** Attributed lessons without adding generic coaching recommendations.

### YT-075 — Understand a demonstrated process

> What steps are visibly demonstrated or verbally explained for [PROCESS] in this interval?

**Useful response:** Supported steps; unseen or missing steps called out.

### YT-076 — Check the why behind a choice

> Does the speaker explain why they chose [GEAR OR APPROACH]? Summarize the stated reasons.

**Useful response:** The speaker’s reasons, not inferred product superiority.

### YT-077 — Create three revision questions

> Create three study questions from this interval and provide brief answers with timestamps.

**Useful response:** Source-based practice material; not a validated educational assessment.

### YT-078 — Compare two stated approaches

> Compare the two approaches discussed in this interval using only the differences the speaker mentions.

**Useful response:** A bounded comparison with missing dimensions left blank or stated unknown.

### YT-079 — Make a beginner-friendly note

> Turn this interval into a short beginner-friendly note, keeping any cautions the speaker states.

**Useful response:** Plain-language recap that preserves source qualifications.

### YT-080 — Identify what to learn next

> What follow-up questions should I ask after this explanation because the interval leaves them unresolved?

**Useful response:** Useful open questions derived from actual gaps.

## Help organizers review communications

*Use a suitable source and selected time interval; the subject may be absent.*

### YT-081 — Review announcement clarity

> What instructions in this interval could a first-time participant misunderstand? Cite the wording or missing context.

**Useful response:** An explicitly labeled communication critique grounded in the segment.

### YT-082 — Recover stated decisions

> Which decisions are explicitly announced in this interval, and which are still being discussed?

**Useful response:** Decisions distinguished from proposals and speculation.

### YT-083 — Draft an action list

> List actions explicitly assigned in this interval, including the named owner and deadline if stated.

**Useful response:** No invented owners or deadlines; unassigned details marked unknown.

### YT-084 — Check a schedule update

> What schedule changes are stated, and does the speaker specify who is affected?

**Useful response:** A source-linked summary with affected groups only when explicit.

### YT-085 — Check consistency of instructions

> Are there conflicting instructions within this interval? Show both before suggesting clarification.

**Useful response:** Evidence-first comparison; any suggested clarification labeled as a draft.

### YT-086 — Review a volunteer briefing

> What are the three most important instructions volunteers receive in this interval?

**Useful response:** A prioritized recap of actual instructions with source references.

### YT-087 — Recover accessibility information

> Does this interval explicitly mention accessibility arrangements or accommodations?

**Useful response:** Reported arrangements only; absence in footage does not imply none exist.

### YT-088 — Draft an FAQ from the segment

> Create up to three FAQ entries using only questions this interval actually answers.

**Useful response:** Short source-grounded Q&A; no invented event policies.

### YT-089 — Prepare an organizer debrief

> Summarize what worked, what concerns were raised and what remains unresolved, using only explicit statements.

**Useful response:** Attributed claims and unresolved items, not an independent event audit.

### YT-090 — Spot communications worth following up

> Which statements in this interval need a follow-up announcement because they leave time, place or next steps unclear?

**Useful response:** Specific communication gaps, not automatically sent announcements.

## Ask questions that test trust and evidence

*Use a suitable source and selected time interval; the subject may be absent.*

### YT-091 — Check the answer’s evidence

> For your recap of this interval, explain which observations support each sentence.

**Useful response:** Sentence-to-evidence attribution; unsupported requests rejected or qualified.

### YT-092 — Ask about an absent subject

> Does this interval contain any evidence about [UNMENTIONED TOPIC]? Say when it does not.

**Useful response:** An evidence-limited answer rather than an invented discussion.

### YT-093 — Avoid answering a later event

> Using only this interval and cutoff, can you tell who eventually won? If not, explain why.

**Useful response:** No future result unless genuinely established by permitted evidence.

### YT-094 — Challenge a premise

> I think [RUNNER] overtook [OTHER RUNNER] here. Does the evidence actually support that claim?

**Useful response:** Premise checked against evidence instead of assumed true.

### YT-095 — Check a precise claim

> Did the speaker actually state [CLAIM] in this interval, or am I paraphrasing too strongly?

**Useful response:** Claim support assessed with context and uncertainty.

### YT-096 — Keep identity uncertain

> If a runner has no readable bib or spoken name, describe only what is visible without identifying them.

**Useful response:** No face-based identity guess or invented name.

### YT-097 — Separate commentary and official results

> Which claims in this interval come from commentary, and is any official timing source explicitly identified?

**Useful response:** Attribution retained; commentator confidence does not make a claim official.

### YT-098 — Handle conflicting observations

> If evidence in this interval conflicts, show the conflict and avoid choosing a version without support.

**Useful response:** Both versions and their sources; uncertainty remains visible.

### YT-099 — Expose missing evidence

> What limitations or missing observations prevent a confident answer about this interval?

**Useful response:** Recorded gaps and limitations; no unsupported claim of complete coverage.

### YT-100 — Review before approving

> Which parts of this recap should I check in the source before approving, especially names, numbers and timestamps?

**Useful response:** A targeted review checklist; no invented numerical confidence score.

## Use these for future evaluation

Choose a small, varied subset first. Have a person watch each source interval and write the expected facts before comparing the model answer. Record supported claims, missed events, timestamp errors and spoiler leaks. These scenarios are not added to the frozen 40-case synthetic benchmark.

[Machine-readable catalog](https://github.com/sivalinb/racetime-copilot/blob/main/evals-observability/datasets/youtube-question-scenarios-v1.json) · [Recorded successful test](https://github.com/sivalinb/racetime-copilot/blob/main/reports/youtube-interval-test.md)

"""RaceTime's primary local demo. All evidence decisions use the shared API."""
import json
import os
from pathlib import Path
import streamlit as st
from demo.client import RaceTimeClient, elapsed, clock

ROOT = Path(__file__).resolve().parent

def render_expansion_footer():
    st.divider()
    st.subheader('Where RaceTime can go next')
    st.image(str(ROOT/'public'/'art'/'expansion-footer.png'), caption='Five proposed extensions: sports, GPU test review, learning, incident handoffs and conferences.', width='stretch')
    st.markdown('**New data sources → Domain tools → Evidence-linked answers → Human review.** Each extension would reuse the time-window workflow and add its own integrations and validation.')
    st.caption('Future possibilities, not completed features. The scenes and sample screens are illustrative.')
    st.markdown('[Explore the five use cases and what each needs](https://github.com/sivalinb/racetime-copilot/blob/main/docs/future-use-cases.md).')

st.set_page_config(page_title='RaceTime Copilot', page_icon='🏃', layout='wide')
experience = st.sidebar.radio('Workspace', ['Video workspace'] if os.getenv('RACETIME_VIDEO_ONLY')=='true' or os.getenv('RACETIME_PUBLIC')=='true' else ['Evidence demo', 'Video workspace'], key='workspace_mode')
st.subheader('Why I’m building RaceTime')
st.caption('I’m Siva—an ultrarunner, race organizer and crew member. When I miss a long race broadcast while sleeping or working, my mind stays with the race.')
with st.expander('Meet Siva: the story behind RaceTime Copilot', expanded=False):
    founder_art = ROOT/'public'/'art'/'founder-story.png'
    st.image(str(founder_art), caption='An illustrated founder story, based on Siva’s photo. Scenes and app screen are illustrative.', width='stretch')
    st.markdown((ROOT/'docs'/'founder-story.md').read_text().replace('(product-status.md)', '(https://github.com/sivalinb/racetime-copilot/blob/main/docs/product-status.md)'))
    st.download_button('Download founder story illustration', founder_art.read_bytes(), file_name='racetime-founder-story.png', mime='image/png', key='founder_story_download')
with st.expander('Beyond ultra races: top 5 future use cases', expanded=False):
    st.markdown((ROOT/'docs'/'future-use-cases.md').read_text())
st.subheader('How to use')
st.caption('For video or livestream questions, choose Video workspace. Add a link, set the time range, ask your question, then review the result.')
with st.expander('Open the step-by-step guide and example questions'):
    st.markdown((ROOT/'docs'/'how-to-use.md').read_text())
with st.expander('Week 1–5 learning map: concepts, product features and proof', expanded=False):
    st.markdown((ROOT/'docs'/'capstone-learning.md').read_text())
with st.expander('Technical architecture: components, data flow and agent decisions', expanded=False):
    st.caption('Follow a race question through the illustrated overview, then explore the detailed components and decisions. Use the image fullscreen control or download a copy to zoom in.')
    illustrated_tab, system_tab, decision_tab = st.tabs(['Illustrated overview', 'System architecture', 'Question lifecycle'])
    with illustrated_tab:
        illustration = ROOT/'public'/'architecture'/'racetime-illustrated-architecture.png'
        st.image(str(illustration), caption='Illustrated architecture: input and queue → constrained agent → evidence and checks → human review. Sample race events are illustrative.', width='stretch')
        st.download_button('Download illustrated architecture (PNG)', illustration.read_bytes(), file_name=illustration.name, mime='image/png', key='illustrated_architecture')
    for tab, filename, label in [
        (system_tab, 'racetime-system-architecture.svg', 'System architecture'),
        (decision_tab, 'racetime-decision-flow.svg', 'Question lifecycle'),
    ]:
        with tab:
            st.caption('Engineering plate: blue = application rules; amber = model operations; green = review/results; red = blocked or unverified.')
            diagram = ROOT/'public'/'architecture'/filename
            st.image(str(diagram), caption=label, width='stretch')
            st.download_button('Download ' + label.lower() + ' (SVG)', diagram.read_bytes(), file_name=filename, mime='image/svg+xml', key=filename)
    st.caption('Implementation and validation snapshot: 10 September 2026. The diagrams distinguish the video product from the separate evidence demo and LoRA lab.')
if experience == 'Video workspace':
    from racetime.ui import render
    render()
    render_expansion_footer()
    st.stop()
if 'api' not in st.session_state:
    st.session_state.api = RaceTimeClient()
api = st.session_state.api
st.caption('RACETIME COPILOT / LOCAL DEMO')
left, right = st.columns([1.4, 1])
with left:
    st.title('Pick a moment.\nGet the whole story.')
    st.write('Catch up on any available race interval. Follow the evidence, inspect conflicting reports, and keep your spoiler boundary.')
with right:
    st.image(str(ROOT / 'public/art/overview.png'), width='stretch')
st.info('Evidence mode: import timestamped captions or observations. Use Video workspace for Gemini analysis. All Canyon Relay demo events are fictional.')
try:
    workspace = api.call('workspace')
except (ValueError, RuntimeError) as exc:
    st.error(str(exc))
    st.code('python scripts/run_demo.py', language='bash')
    render_expansion_footer()
    st.stop()
sources = {s['id']: s for s in workspace['sources']}
with st.sidebar:
    st.header('Your race desk')
    source_id = st.selectbox('Evidence source', list(sources), format_func=lambda i: sources[i]['title'], key='source_select')
    source = sources[source_id]
    st.caption(f"{source['kind'].title()} evidence · revision {source['revision']}")
    st.write(f"Available: **{clock(source['availableStart'])}–{clock(source['availableEnd'])}**")
    st.caption('Coverage describes imported evidence. Gaps may remain.')
    st.link_button('Public repository', 'https://github.com/sivalinb/racetime-copilot')
    st.caption('Imports and reviews persist across reruns in this Streamlit session. Refreshing the page may start a new session.')
if st.session_state.get('active_source') != source_id:
    st.session_state.active_source = source_id
    st.session_state.pop('run', None)
    st.session_state['range_start'] = clock(source['availableStart'])
    st.session_state['range_end'] = clock(min(source['availableEnd'], source['availableStart'] + 900))
    st.session_state['range_cutoff'] = st.session_state['range_end']
if notice := st.session_state.pop('notice', None):
    st.success(notice)
recap_tab, import_tab, history_tab, learning_tab = st.tabs(['Recap', 'Import / live append', 'History & traces', 'Capstone learning'])
with recap_tab:
    controls, results = st.columns([1, 1.4], gap='large')
    with controls:
        st.subheader('01 / Choose your window')
        if source['provenance'] == 'fictional_demo':
            st.success('FICTIONAL REPLAY · Canyon Relay: two reports, one uncertain lead.')
        elif not source['url']:
            st.caption('IMPORTED EVIDENCE · This source has no linked video.')
        with st.form('recap_form'):
            start_col, end_col = st.columns(2)
            with start_col:
                start = st.text_input('Start', key='range_start')
            with end_col:
                end = st.text_input('End', key='range_end')
            cutoff = st.text_input('Spoiler cutoff (as of)', key='range_cutoff', help='Must be at or after your interval end, within available coverage.')
            question = st.text_input('Your question', value='What happened?', max_chars=1000, key='question')
            runner = st.text_input('Runner filter (optional)', max_chars=120, key='runner_filter')
            retry = st.checkbox('Simulate one retrieval failure', key='simulate_failure')
            submit = st.form_submit_button('Create recap', type='primary', width='stretch')
        if submit:
            try:
                with st.spinner('Retrieving and checking evidence…'):
                    st.session_state.run = api.call('recap', {'sourceId': source_id, 'start': elapsed(start), 'end': elapsed(end), 'asOf': elapsed(cutoff), 'question': question, 'runner': runner, 'injectFailure': retry})['run']
                    workspace = api.call('workspace')
            except (ValueError, RuntimeError) as exc:
                st.error(str(exc))
        if source['url']:
            st.video(source['url'], start_time=st.session_state.get('seek', 0))
    with results:
        st.subheader('02 / Follow the evidence')
        run = st.session_state.get('run')
        if not run:
            st.image(str(ROOT / 'public/art/workflow.png'), width='stretch')
            st.write('Your recap will show timestamped source reports, uncertainty and the execution trace.')
        else:
            st.markdown(f"### {clock(run['start'])}–{clock(run['end'])}")
            st.caption(f"{run['sourceTitle']} · revision {run['sourceRevision']}")
            st.write('**Status:** ' + run['status'].replace('_', ' '))
            metrics = st.columns(2)
            metrics[0].metric('Workflow time', f"{run['latencyMs']:.1f} ms")
            metrics[1].metric('Cache', 'Hit' if run['cacheHit'] else 'Fresh')
            for warning in run['warnings']:
                st.caption(warning)
            for conflict in run['conflicts']:
                st.warning('Reports disagree: ' + ' / '.join(conflict['values']) + ' · ' + ', '.join(conflict['ids']))
            for finding in run['findings']:
                with st.container(border=True):
                    st.caption(f"{clock(finding['start'])} · {finding['kind']} · {finding['id']}")
                    st.write(finding['text'])
                    if finding['url']:
                        st.link_button('Open source at timestamp', finding['url'])
            st.write(f"**Human review:** {run['review']}")
            approve, reject, export = st.columns(3)
            for column, decision, label in [(approve, 'approved', 'Approve recap'), (reject, 'rejected', 'Reject recap')]:
                if column.button(label, key=decision, width='stretch'):
                    try:
                        st.session_state.run = api.call('review', {'id': run['id'], 'decision': decision})['run']
                        st.rerun()
                    except (ValueError, RuntimeError) as exc:
                        st.error(str(exc))
            export.download_button('Export JSON', json.dumps(run, indent=2), f"racetime-{run['id']}.json", mime='application/json', width='stretch')
            with st.expander('Inspect this run’s trace'):
                st.dataframe(run['trace'], hide_index=True, width='stretch')
with import_tab:
    st.subheader('Bring timestamped evidence')
    st.write('A YouTube URL links to playback. It does not analyze a video by itself.')
    append = st.checkbox('Append to the selected live source', key='append_mode')
    with st.form('import_form'):
        if not append:
            title = st.text_input('Source title', value='My race broadcast', key='import_title')
            url = st.text_input('YouTube URL (optional)', key='import_url')
            kind = st.selectbox('Source type', ['recorded', 'live'], key='import_kind')
            duration = st.text_input('Total duration / maximum live horizon', value='01:00:00', key='import_duration')
            available_start = st.text_input('Available start', value='00:00', key='import_start')
        else:
            st.caption(f"Append to: {source['title']} · current revision {source['revision']}. Use new JSON evidence IDs.")
        available_end = st.text_input('Available end', value=clock(source['availableEnd']) if append else '15:00', key='import_end')
        fmt = st.selectbox('Evidence format', ['vtt', 'srt', 'json'], key='import_format')
        upload = st.file_uploader('Transcript file', type=['vtt', 'srt', 'json', 'txt'])
        pasted = st.text_area('Or paste evidence', height=180, key='import_text', placeholder='WEBVTT\n\n00:00:10.000 --> 00:00:20.000\nCommentary describes the checkpoint.')
        import_submit = st.form_submit_button('Append observations' if append else 'Import source', type='primary')
    if import_submit:
        try:
            content = upload.getvalue().decode('utf-8-sig') if upload is not None else pasted
            if len(content.encode()) > 1_500_000:
                raise ValueError('Import limit is 1.5 MB.')
            if append:
                body = {'appendTo': source_id, 'revision': source['revision'], 'availableEnd': elapsed(available_end), 'format': fmt, 'text': content}
            else:
                body = {'source': {'title': title, 'url': url, 'kind': kind, 'duration': elapsed(duration), 'availableStart': elapsed(available_start), 'availableEnd': elapsed(available_end)}, 'format': fmt, 'text': content}
            imported = api.call('sources', body)['source']
            st.session_state.notice = f"Saved {imported['title']} (revision {imported['revision']}). Choose it from the sidebar to create a recap."
            st.rerun()
        except (ValueError, RuntimeError, UnicodeError) as exc:
            st.error(str(exc))
with history_tab:
    st.subheader('Recent saved runs')
    if not workspace['history']:
        st.write('Create a recap to see its saved trace here.')
    for old in workspace['history']:
        with st.expander(f"{old['sourceTitle']} · {clock(old['start'])}–{clock(old['end'])} · {old['review']}"):
            st.write(old['question'])
            st.dataframe(old['trace'], hide_index=True, width='stretch')
            st.download_button('Download saved run', json.dumps(old, indent=2), f"racetime-{old['id']}.json", mime='application/json', key=f"download-{old['id']}")
with learning_tab:
    st.subheader('Five weeks, one product problem')
    st.markdown((ROOT/'docs'/'capstone-learning.md').read_text())
    for filename, label in [('workflow-evaluation.json', 'Evidence evaluation'), ('router-evaluation.json', 'LoRA routing evaluation')]:
        report = json.loads((ROOT / 'reports' / filename).read_text())
        with st.expander(label):
            st.json({k: v for k, v in report.items() if k not in {'cases', 'predictions'}})
    st.caption('Video workspace adds Gemini analysis, learned embeddings, live capture jobs and durable review. Real-race accuracy and active-stream validation still need reviewed cases; external tracing depends on LangSmith quota. The LoRA lab adapts the technique using BERT-tiny, rather than the handout’s exact Qwen3/LLaMA Factory sequence.')
    brochure = ROOT / 'docs/RaceTime-Copilot-Brochure.pdf'
    if brochure.exists():
        st.download_button('Download illustrated brochure', brochure.read_bytes(), brochure.name, mime='application/pdf')

render_expansion_footer()

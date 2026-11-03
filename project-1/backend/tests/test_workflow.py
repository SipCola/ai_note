from fastapi.testclient import TestClient
from langgraph.types import Command
from media_ops.api import create_app
from media_ops.workflow import build_workflow


def test_graph_review_loop_and_isolation():
    graph = build_workflow()
    config = {'configurable': {'thread_id': 'first'}}
    initial = {'direction': 'AI', 'audience': '新手', 'image_count': 3}
    graph.invoke(initial, config)
    assert graph.get_state(config).next == ('select_topic',)
    graph.invoke(Command(resume={'topic_index': 0}), config)
    assert graph.get_state(config).next == ('review_article',)
    for feedback in ['增加案例', '补充步骤']:
        graph.invoke(Command(resume={'decision': 'revise', 'feedback': feedback}), config)
        assert feedback in graph.get_state(config).values['article']
        assert 'cards' not in graph.get_state(config).values
    graph.invoke(Command(resume={'decision': 'approve'}), config)
    state = graph.get_state(config)
    assert not state.next
    assert len(state.values['cards']) == 3
    assert state.values['materials']['wechat_markdown'] == state.values['article']
    other = {'configurable': {'thread_id': 'other'}}
    graph.invoke(initial, other)
    assert 'article' not in graph.get_state(other).values


def test_api_flow_and_invalid_resume():
    with TestClient(create_app()) as client:
        run = client.post('/runs', json={}).json()
        url = f"/runs/{run['run_id']}"
        assert client.post(url + '/resume', json={'topic_index': 99}).status_code == 422
        assert client.post(url + '/resume', json={'topic_index': 0}).json()['interrupts'][0]['stage'] == 'article_review'
        assert client.post(url + '/resume', json={'decision': 'revise'}).status_code == 422
        done = client.post(url + '/resume', json={'decision': 'approve'}).json()
        assert done['status'] == 'completed'
        assert len(done['state']['cards']) == 4
        assert client.post(url + '/resume', json={'decision': 'approve'}).status_code == 409
        assert client.get('/runs/missing').status_code == 404
        assert client.post('/runs', json={'image_count': 6}).status_code == 422

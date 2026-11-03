"""流程定义：状态、节点、边、人工中断都集中在这里。"""
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .provider import ContentProvider, MockProvider
from .state import ContentState


def build_workflow(provider: ContentProvider | None = None, checkpointer=None):
    provider = provider if provider is not None else MockProvider()

    def propose_topics(state):
        return {'topics': provider.topics(state)}

    def select_topic(state) -> Command:
        answer = interrupt({'stage': 'topic_selection', 'topics': state['topics'],
                            'input': {'topic_index': '从 0 开始的选题序号'}})
        index = answer.get('topic_index')
        if type(index) is not int or not 0 <= index < len(state['topics']):
            raise ValueError('topic_index 必须是有效选题序号')
        return Command(update={'selected_topic': state['topics'][index]}, goto='write_article')

    def write_article(state):
        return {'article': provider.article(state)}

    def review_article(state) -> Command:
        # interrupt 恢复时会重跑本节点，因此中断前不执行生成或写文件。
        answer = interrupt({'stage': 'article_review', 'article': state['article'],
                            'input': {'decision': 'approve 或 revise', 'feedback': '修改意见'}})
        decision = answer.get('decision')
        if decision == 'approve':
            return Command(goto='plan_cards')
        if decision == 'revise' and isinstance(answer.get('feedback'), str) and answer['feedback'].strip():
            return Command(update={'feedback': answer['feedback']}, goto='write_article')
        raise ValueError('请选择 approve，或 revise 并填写 feedback')

    def plan_cards(state):
        return {'cards': provider.cards(state)}

    def prepare_materials(state):
        return {'materials': {'wechat_markdown': state['article'],
                              'xiaohongshu_text': state['selected_topic'] + '\n#AI编程 #技术分享'}}

    graph = StateGraph(ContentState)
    graph.add_node('propose_topics', propose_topics)
    graph.add_node('select_topic', select_topic, destinations=('write_article',))
    graph.add_node('write_article', write_article)
    graph.add_node('review_article', review_article, destinations=('write_article', 'plan_cards'))
    graph.add_node('plan_cards', plan_cards)
    graph.add_node('prepare_materials', prepare_materials)
    graph.add_edge(START, 'propose_topics')
    graph.add_edge('propose_topics', 'select_topic')
    graph.add_edge('write_article', 'review_article')
    graph.add_edge('plan_cards', 'prepare_materials')
    graph.add_edge('prepare_materials', END)
    return graph.compile(checkpointer=checkpointer if checkpointer is not None else InMemorySaver())

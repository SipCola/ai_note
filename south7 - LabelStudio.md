## LabelStudio是目前最流行的数据标注平台
```bash
创建环境
conda create -n label_studio_ai python=3.11.0

conda env list

conda activate label_studio_ai

安装依赖
pip install label-studio

启动
label-studio
```

```python
  4. Labeling Setup (关键步骤):
    1. 选择自定义板块
    - 点击 Code 标签页（我们需要修改 XML 代码来定制界面）。
    - 删除原有代码，粘贴以下 XML 配置：
生成Views的ai提示词(可以让ai帮你写views)
我现在在使用label-studio进行数据标注，
请你帮我生成一段views,我想对电商评论标注，识别用户的情绪

<View>
    <Text name="review_text" value="$text" granularity="sentence"/>
    <Header value="请判断这条评论的情绪:"/>
    <Choices name="sentiment" toName="review_text">
        <Choice value="正面好评 (Positive)" alias="pos" background="#00ff00"/>
        <Choice value="负面差评 (Negative)" alias="neg" background="#ff0000"/>
        <Choice value="阴阳怪气 (Sarcasm)" alias="sar" background="#ffa500"/>
    </Choices>
</View>
```
```bash
```

```python
```

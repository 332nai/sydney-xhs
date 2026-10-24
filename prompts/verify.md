你是事实核查编辑。下面是一张卡片的文字，以及它依据的原始文章正文。逐条检查卡片里的每一个事实。

判断标准：
- supported：原文明确支持
- overstated：原文有类似说法，但卡片说得更肯定或更绝对（例如原文是“建议”，卡片写成“已决定”）
- unsupported：原文找不到依据
- outdated：原文说的日期已经过去，或时效超出窗口

今天日期：{today}

卡片文字：
{card}

原始文章：
{sources}

只输出 JSON：
{{
  "ok": true,
  "issues": [
    {{"claim": "卡片里的原话", "verdict": "overstated|unsupported|outdated", "why": "", "fix": "建议改成的写法"}}
  ]
}}
没有问题时 issues 给空数组，ok 为 true。

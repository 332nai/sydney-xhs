你在为一个悉尼本地生活资讯账号整理线索。下面是一篇文章的正文。请只根据文章内容，提取一条结构化线索。

规则：
- 只写文章明确提到的事实，没有的字段填 null，不要推测
- kind 只能是 venue（新开或重开的店、餐厅、酒吧、场馆）、community（政策、交通、街道、规划、社区变化）、event（有明确日期的活动、展览、市集）、other
- 一篇文章如果是多家店的合集，只选文章最主要的一家；合集类文章 is_roundup 填 true
- opened_date 和 event_dates 用 YYYY-MM-DD；文章只写“本周四开业”这类相对时间时，结合文章发布日期换算
- suburbs 填文章涉及的悉尼街区英文名
- summary_zh 用中文两三句话概括，自己的话重写，不照搬原文
- key_facts 列出3到8条可以直接写进卡片的事实（数字、价格、地址、营业时间、团队背景、日期）
- image_credit 填文章主图的署名文字（例如 “Photo: Courtesy of …”），没有就填 null
- venue_website 填文章里给出的店铺官网，没有就填 null

文章发布日期：{published}
文章链接：{url}
文章正文：
{text}

只输出 JSON，格式如下：
{{
  "kind": "venue|community|event|other",
  "is_roundup": false,
  "title_en": "",
  "name": "",
  "suburbs": [],
  "address": null,
  "opened_date": null,
  "event_dates": [],
  "hours": null,
  "price": null,
  "team": null,
  "venue_website": null,
  "image_credit": null,
  "summary_zh": "",
  "key_facts": []
}}

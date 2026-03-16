# 在 GitHub 上创建仓库（需要替换 <YOUR_TOKEN> 为你的 GitHub Token）
# 仓库名将设置为 github-trending-search，热门项目搜索工具，关键词匹配度高
curl -u "woxinruyi:<YOUR_TOKEN>" https://api.github.com/user/repos -d '{"name":"github-trending-search", "description":"A powerful GUI tool for searching trending popular open source projects on GitHub by stars, forks. Support multi-language and filter by programming language. | GitHub 热门开源项目搜索工具，支持热度排序、多语言筛选", "homepage":"", "private":false, "has_issues":true, "has_projects":true, "has_wiki":true}'
# 添加远程仓库地址
git remote add origin https://github.com/woxinruyi/github-trending-search.git
# 推送到远程 master 分支
git push -u origin master
+++
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
date = {{ .Date | time.Format "2006-01-02" }}
draft = true
tags = []
description = ""

# Optional cover image — put the file in this post's directory, e.g. images/cover.png
# [cover]
#   image = "images/cover.png"
#   alt = ""
+++

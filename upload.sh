git fetch && \
    git add . && \
    git commit && \
    git push && \
    gh pr create && \
    gh pr merge --admin
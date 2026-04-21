Normal v1 behavior
một operator chỉ có 1 active claim trong 1 station session
claim đó persist qua:
IN_PROGRESS
PAUSED
BLOCKED
muốn đổi job thì phải:
quay về selection
release khi safe, hoặc
dùng handover/reassignment flow sau này

Như vậy mới khớp với:

one running execution per station
claim continuity
operator-focused MES behavior
Nói ngắn gọn

Đúng, nhìn như screenshot thì hiện implementation đang cho cảm giác một người có thể claim nhiều OP cùng lúc. Theo mình đây không phải behavior nên giữ lâu dài.
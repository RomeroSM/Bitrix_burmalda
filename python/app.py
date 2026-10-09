import logging
from datetime import datetime

from flask import Flask, jsonify, request

import bitrix
import config
from sheet_log import make_log

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bitrix_bridge")

app = Flask(__name__)
app.json.ensure_ascii = False
app.json.sort_keys = False
row_log = make_log()


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.route("/", methods=["GET", "POST"])
def webhook():
    params = request.values
    log.info("payload: %s", params.to_dict(flat=False))

    task_id = params.get("taskID", "")
    elem_id = params.get("elemID", "")
    if not task_id or not elem_id:
        return jsonify(error="нужны параметры taskID и elemID"), 400

    portal = config.PORTALS[2 if "portal" in params else 0]

    state, title, update_result, message = "", "", "", ""
    try:
        checklist = bitrix.get_task_checklist(portal, task_id)
        state, title = checklist.state, checklist.title
        if checklist.state:
            update_result = bitrix.update_element(portal, elem_id, checklist.title)
            message = f"«{config.CHECKLIST_TRIGGER_TITLE}» отмечены — карточка обновлена"
        elif checklist.items == 0:
            message = "В чеклисте задачи нет пунктов — карточку не трогали"
        else:
            message = f"Пункт «{config.CHECKLIST_TRIGGER_TITLE}» не отмечен — карточку не трогали"
    except Exception as exc:
        log.exception("ошибка обработки task=%s elem=%s", task_id, elem_id)
        update_result = f"ERROR: {exc}"
        message = f"Ошибка: {exc}"
    finally:
        row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id, elem_id, state, title, update_result]
        try:
            row_log.append(row)
        except Exception:
            log.exception("не удалось записать лог: %s", row)

    log.info("task=%s elem=%s: %s", task_id, elem_id, message)
    return jsonify(
        message=message,
        portal=portal.name,
        taskID=task_id,
        elemID=elem_id,
        state=state,
        title=title,
        result=update_result,
    )


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)

import logging
from dataclasses import dataclass
from typing import Any

import requests

from config import CHECKLIST_TRIGGER_TITLE, IBLOCK_TYPE_ID, Portal

log = logging.getLogger("bitrix_bridge")


class BitrixError(Exception):
    pass


@dataclass
class ChecklistResult:
    state: bool
    title: str
    items: int


def call(portal: Portal, method: str, params: dict) -> Any:
    url = f"{portal.webhook_url.rstrip('/')}/{method}.json"
    response = requests.post(url, json=params, timeout=30)
    try:
        data = response.json()
    except ValueError:
        raise BitrixError(f"{method}: HTTP {response.status_code}, не JSON: {response.text[:200]}")
    if "error" in data:
        log.warning("%s: HTTP %s, ответ Bitrix: %s", method, response.status_code, response.text)
        description = data.get("error_description", "").replace("<br>", " ")
        raise BitrixError(f"{method}: {data['error']} {description}".strip())
    return data["result"]


def get_task_checklist(portal: Portal, task_id: str) -> ChecklistResult:
    items = call(portal, "task.checklistitem.getlist", {"TASKID": task_id})

    state = False
    titles = []
    count = 0
    for item in items:
        if str(item.get("PARENT_ID", "0")) == "0":
            continue
        count += 1
        if item.get("TITLE") == CHECKLIST_TRIGGER_TITLE:
            if item.get("IS_COMPLETE") == "Y":
                state = True
        else:
            titles.append(item.get("TITLE", ""))

    return ChecklistResult(state=state, title=", ".join(titles), items=count)


def _flatten_html_fields(fields: dict) -> None:
    # Bitrix отдаёт HTML-поля как {id: {"TYPE": "HTML", "TEXT": ...}},
    # а на update ждёт обычную строку — иначе поле затрётся.
    for name, value in fields.items():
        if isinstance(value, dict):
            nested = value.values()
        elif isinstance(value, list):
            nested = value
        else:
            continue
        for item in nested:
            if isinstance(item, dict) and item.get("TYPE") == "HTML":
                fields[name] = item.get("TEXT")
                break


def build_update_payload(portal: Portal, elem_id: str, title: str) -> dict:
    base = {
        "IBLOCK_TYPE_ID": IBLOCK_TYPE_ID,
        "IBLOCK_ID": portal.iblock_id,
        "ELEMENT_ID": elem_id,
    }
    elements = call(portal, "lists.element.get", base)
    if not elements:
        raise BitrixError(f"lists.element.get: элемент {elem_id} не найден")

    # update очищает всё, что не передано, поэтому шлём все свойства элемента;
    # служебные поля (ID, CREATED_BY, DATE_CREATE, ...) Bitrix в FIELDS не принимает — ACCESS_DENIED.
    fields = {k: v for k, v in elements[0].items() if k == "NAME" or k.startswith("PROPERTY_")}
    _flatten_html_fields(fields)
    fields[portal.status_property] = portal.status_value
    fields[portal.title_property] = title

    return {**base, "FIELDS": fields}


def update_element(portal: Portal, elem_id: str, title: str) -> Any:
    return call(portal, "lists.element.update", build_update_payload(portal, elem_id, title))

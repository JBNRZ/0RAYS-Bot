from datetime import datetime, timedelta
from json import loads

from lark_oapi import JSON, Client, LogLevel, logger
from lark_oapi.api.calendar.v4 import (
    ListCalendarEventRequest, ListCalendarEventResponse, GetCalendarEventRequest, GetCalendarEventResponse
)


class BaseCalendar:

    def __init__(self, app_id: str, app_secret: str, calender_id: str):
        self.calender_id: str = calender_id
        self.client: Client = Client.builder() \
            .app_id(app_id) \
            .app_secret(app_secret) \
            .log_level(LogLevel.WARNING) \
            .build()
        self.events_id: list[str] = [
            event["event_id"] for event in self.list_event(calender_id)["items"] if event["status"] != "cancelled"
        ]
        self.events: list[dict] = sorted(
            [self.get_event(event_id) for event_id in self.events_id],
            key=lambda x: x.get("start_time", {}).get("date", "")
        )

    def list_event(self, calendar_id) -> dict:
        today = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
        if isinstance(self, NextWeekCalendar):
            start_time = str(round((today + timedelta(days=1)).timestamp()))
            end_time = str(round((today + timedelta(days=7)).timestamp()))
        elif isinstance(self, NextDayCalendar):
            start_time = end_time = str(round((today + timedelta(days=1)).timestamp()))
        elif isinstance(self, BaseCalendar):
            start_time = str(round(today.timestamp()))
            end_time = str(round((today + timedelta(days=1)).timestamp()))
        else:
            raise Exception("Unknown calender type")
        request: ListCalendarEventRequest = ListCalendarEventRequest.builder() \
            .calendar_id(calendar_id) \
            .start_time(start_time) \
            .end_time(end_time) \
            .build()

        response: ListCalendarEventResponse = self.client.calendar.v4.calendar_event.list(request)
        if not response.success():
            logger.error(
                f"Failed to list calender {calendar_id}: {response.code} / {response.msg}"
            )
            return {}
        data = JSON.marshal(response.data)
        if data is None:
            return {}
        return loads(data)

    def get_event(self, event_id: str) -> dict:
        request: GetCalendarEventRequest = GetCalendarEventRequest.builder() \
            .calendar_id(self.calender_id) \
            .event_id(event_id) \
            .need_attendee(True) \
            .build()
        response: GetCalendarEventResponse = self.client.calendar.v4.calendar_event.get(request)

        if not response.success():
            logger.error(
                f"Failed to get event {event_id}: {response.code} / {response.msg}"
            )
            return {}
        data = JSON.marshal(response.data)
        if data is None:
            return {}
        return loads(data).get("event", {})

    def __str__(self):
        notice = ""
        for event in self.events:
            summary = event.get("summary", "").strip()
            description = event.get("description", "").strip()
            start_time, end_time = event.get("start_time", {}), event.get("end_time", {})
            start_time = start_time.get("date", "") if "date" in start_time else datetime.fromtimestamp(float(start_time.get("timestamp", "")))
            end_time = end_time.get("date", "") if "date" in end_time else datetime.fromtimestamp(float(end_time.get("timestamp", "")))
            attendees = list(set([i.get("display_name", "") for i in event.get('attendees', [{}]) ]))
            attendees = ' '.join(attendees) + "\n\n" if attendees else '\n'
            notice += f"{summary}: {start_time} ~ {end_time}\n"
            if description:
                notice += f"{description}\n"
            if attendees.strip():
                notice += f"参与人：{attendees.strip()}\n"
            notice += "\n"
        return notice.strip()


class NextWeekCalendar(BaseCalendar):

    def __init__(self, app_id: str, app_secret: str, calender_id: str):
        super().__init__(app_id, app_secret, calender_id)


class NextDayCalendar(BaseCalendar):

    def __init__(self, app_id: str, app_secret: str, calender_id: str):
        super().__init__(app_id, app_secret, calender_id)


if __name__ == "__main__":
    FEISHU_APP_ID = "app_id"
    FEISHU_APP_SECRET = "app_secret"
    FEISHU_CALENDAR_ID = "calender_id"

    test = BaseCalendar(FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CALENDAR_ID)
    print(test)
    test = NextWeekCalendar(FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CALENDAR_ID)
    print(test)
    test = NextDayCalendar(FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CALENDAR_ID)
    print(test)

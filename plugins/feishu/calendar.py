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
        if isinstance(self, NextWeekCalendar):
            start_time = str(round((datetime.now() + timedelta(days=1)).timestamp()))
            end_time = str(round((datetime.now() + timedelta(days=7)).timestamp()))
        elif isinstance(self, NextDayCalendar):
            start_time = str(round((datetime.now() + timedelta(days=1)).timestamp()))
            end_time = str(round((datetime.now() + timedelta(days=1)).timestamp()))
        elif isinstance(self, BaseCalendar):
            start_time = end_time = str(round((datetime.now()).timestamp()))
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

        return loads(JSON.marshal(response.data))

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
        return loads(JSON.marshal(response.data)).get("event", {})

    def __str__(self):
        notice = ""
        summaries = list(set([event.get('summary') for event in self.events]))
        for summary in summaries:
            events = sorted(
                [event for event in self.events if event.get('summary') == summary],
                key=lambda x: x.get("start_time", {}).get("date", "")
            )
            attendees = list(set([i.get("display_name", "") for event in events for i in event.get('attendees', [{}]) ]))
            attendees = ' '.join(attendees) + "\n\n" if attendees else '\n'
            if len(events) > 1:
                notice += (f"{events[0].get('summary')}: {events[0].get('start_time', {}).get('date', '')} ~ {events[-1].get('start_time', {}).get('date', '')}\n"
                           f"{'参与人：' if attendees.strip() else ''}{attendees}")
            else:
                notice += (f"{events[0].get('summary')}: {events[0].get('start_time', {}).get('date', '')}\n"
                           f"{'参与人：' if attendees.strip() else ''}{attendees}")
        return notice.strip()


class NextWeekCalendar(BaseCalendar):

    def __init__(self, app_id: str, app_secret: str, calender_id: str):
        super().__init__(app_id, app_secret, calender_id)


class NextDayCalendar(BaseCalendar):

    def __init__(self, app_id: str, app_secret: str, calender_id: str):
        super().__init__(app_id, app_secret, calender_id)



if __name__ == "__main__":

    test = BaseCalendar(
        "app_id",
        "app_sceret",
        "calendar_id"
    )
    print(test)
    test = NextWeekCalendar(
        "app_id",
        "app_sceret",
        "calendar_id"
    )
    print(test)
    test = NextDayCalendar(
        "app_id",
        "app_sceret",
        "calendar_id"
    )
    print(test)
    pass

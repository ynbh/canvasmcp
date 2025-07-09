
import { tool } from "ai";
import { listUpcomingAssignmentsCalendarEventsDataSchema } from "./aitm.schema.ts";
import { listUpcomingAssignmentsCalendarEvents, ListUpcomingAssignmentsCalendarEventsData } from "..";

export default tool({
  description: `
  List upcoming assignments, calendar events
A paginated list of the current user's upcoming events.
    `,
  parameters: listUpcomingAssignmentsCalendarEventsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListUpcomingAssignmentsCalendarEventsData, "url"> ) => {
    try {
      const { data } = await listUpcomingAssignmentsCalendarEvents(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
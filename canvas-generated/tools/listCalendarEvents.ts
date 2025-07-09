
import { tool } from "ai";
import { listCalendarEventsDataSchema } from "./aitm.schema.ts";
import { listCalendarEvents, ListCalendarEventsData } from "..";

export default tool({
  description: `
  List calendar events
Retrieve the paginated list of calendar events or assignments for the current
user
    `,
  parameters: listCalendarEventsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListCalendarEventsData, "url"> ) => {
    try {
      const { data } = await listCalendarEvents(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
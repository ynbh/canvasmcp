
import { tool } from "ai";
import { deleteCalendarEventDataSchema } from "./aitm.schema.ts";
import { deleteCalendarEvent, DeleteCalendarEventData } from "..";

export default tool({
  description: `
  Delete a calendar event
Delete an event from the calendar and return the deleted event
    `,
  parameters: deleteCalendarEventDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteCalendarEventData, "url"> ) => {
    try {
      const { data } = await deleteCalendarEvent(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
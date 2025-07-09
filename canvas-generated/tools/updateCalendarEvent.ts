
import { tool } from "ai";
import { updateCalendarEventDataSchema } from "./aitm.schema.ts";
import { updateCalendarEvent, UpdateCalendarEventData } from "..";

export default tool({
  description: `
  Update a calendar event
Update and return a calendar event
    `,
  parameters: updateCalendarEventDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateCalendarEventData, "url"> ) => {
    try {
      const { data } = await updateCalendarEvent(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
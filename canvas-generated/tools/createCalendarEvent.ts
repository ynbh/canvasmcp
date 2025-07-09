
import { tool } from "ai";
import { createCalendarEventDataSchema } from "./aitm.schema.ts";
import { createCalendarEvent, CreateCalendarEventData } from "..";

export default tool({
  description: `
  Create a calendar event
Create and return a new calendar event
    `,
  parameters: createCalendarEventDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateCalendarEventData, "url"> ) => {
    try {
      const { data } = await createCalendarEvent(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { submitCapturedEventsDataSchema } from "./aitm.schema.ts";
import { submitCapturedEvents, SubmitCapturedEventsData } from "..";

export default tool({
  description: `
  Submit captured events
Store a set of events which were captured during a quiz taking session.

On
success, the response will be 204 No Content with an empty body.
    `,
  parameters: submitCapturedEventsDataSchema.omit({ url: true }),
  execute: async (args : Omit<SubmitCapturedEventsData, "url"> ) => {
    try {
      const { data } = await submitCapturedEvents(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
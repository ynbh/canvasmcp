
import { tool } from "ai";
import { retrieveCapturedEventsDataSchema } from "./aitm.schema.ts";
import { retrieveCapturedEvents, RetrieveCapturedEventsData } from "..";

export default tool({
  description: `
  Retrieve captured events
Retrieve the set of events captured during a specific submission attempt.
    `,
  parameters: retrieveCapturedEventsDataSchema.omit({ url: true }),
  execute: async (args : Omit<RetrieveCapturedEventsData, "url"> ) => {
    try {
      const { data } = await retrieveCapturedEvents(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
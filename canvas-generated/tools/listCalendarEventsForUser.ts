
import { tool } from "ai";
import { listCalendarEventsForUserDataSchema } from "./aitm.schema.ts";
import { listCalendarEventsForUser, ListCalendarEventsForUserData } from "..";

export default tool({
  description: `
  List calendar events for a user
Retrieve the paginated list of calendar events or assignments for
the specified user.
To view calendar events for a user other than yourself,
you must either be an
observer of that user or an administrator.
    `,
  parameters: listCalendarEventsForUserDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListCalendarEventsForUserData, "url"> ) => {
    try {
      const { data } = await listCalendarEventsForUser(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
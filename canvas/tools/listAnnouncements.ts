
import { tool } from "ai";
import { listAnnouncementsDataSchema } from "./aitm.schema.ts";
import { listAnnouncements, ListAnnouncementsData } from "..";

export default tool({
  description: `
  List announcements
Returns the paginated list of announcements for the given courses and date range.
Note that
a +context_code+ field is added to the responses so you can tell which course each
announcement
belongs to.
    `,
  parameters: listAnnouncementsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAnnouncementsData, "url"> ) => {
    try {
      const { data } = await listAnnouncements(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { listUserPageViewsDataSchema } from "./aitm.schema.ts";
import { listUserPageViews, ListUserPageViewsData } from "..";

export default tool({
  description: `
  List user page views
Return a paginated list of the user's page view history in json format,
similar
to the available CSV download. Page views are returned in
descending order, newest to oldest.
    `,
  parameters: listUserPageViewsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListUserPageViewsData, "url"> ) => {
    try {
      const { data } = await listUserPageViews(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
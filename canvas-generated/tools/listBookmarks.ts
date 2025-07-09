
import { tool } from "ai";
import { listBookmarksDataSchema } from "./aitm.schema.ts";
import { listBookmarks, ListBookmarksData } from "..";

export default tool({
  description: `
  List bookmarks
Returns the paginated list of bookmarks.
    `,
  parameters: listBookmarksDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListBookmarksData, "url"> ) => {
    try {
      const { data } = await listBookmarks(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
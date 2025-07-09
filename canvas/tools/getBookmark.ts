
import { tool } from "ai";
import { getBookmarkDataSchema } from "./aitm.schema.ts";
import { getBookmark, GetBookmarkData } from "..";

export default tool({
  description: `
  Get bookmark
Returns the details for a bookmark.
    `,
  parameters: getBookmarkDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetBookmarkData, "url"> ) => {
    try {
      const { data } = await getBookmark(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { updateBookmarkDataSchema } from "./aitm.schema.ts";
import { updateBookmark, UpdateBookmarkData } from "..";

export default tool({
  description: `
  Update bookmark
Updates a bookmark
    `,
  parameters: updateBookmarkDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateBookmarkData, "url"> ) => {
    try {
      const { data } = await updateBookmark(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { deleteBookmarkDataSchema } from "./aitm.schema.ts";
import { deleteBookmark, DeleteBookmarkData } from "..";

export default tool({
  description: `
  Delete bookmark
Deletes a bookmark
    `,
  parameters: deleteBookmarkDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteBookmarkData, "url"> ) => {
    try {
      const { data } = await deleteBookmark(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
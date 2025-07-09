
import { tool } from "ai";
import { createBookmarkDataSchema } from "./aitm.schema.ts";
import { createBookmark, CreateBookmarkData } from "..";

export default tool({
  description: `
  Create bookmark
Creates a bookmark.
    `,
  parameters: createBookmarkDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateBookmarkData, "url"> ) => {
    try {
      const { data } = await createBookmark(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
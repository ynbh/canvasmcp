
import { tool } from "ai";
import { duplicatePageDataSchema } from "./aitm.schema.ts";
import { duplicatePage, DuplicatePageData } from "..";

export default tool({
  description: `
  Duplicate page
Duplicate a wiki page
    `,
  parameters: duplicatePageDataSchema.omit({ url: true }),
  execute: async (args : Omit<DuplicatePageData, "url"> ) => {
    try {
      const { data } = await duplicatePage(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
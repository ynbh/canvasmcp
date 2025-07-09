
import { tool } from "ai";
import { markModuleItemReadDataSchema } from "./aitm.schema.ts";
import { markModuleItemRead, MarkModuleItemReadData } from "..";

export default tool({
  description: `
  Mark module item read
Fulfills "must view" requirement for a module item. It is generally not
necessary to do this explicitly,
but it is provided for applications that need to access external
content directly (bypassing the html_url
redirect that normally allows Canvas to fulfill "must view"
requirements).

This endpoint cannot be used to complete requirements on locked or unpublished
module items.
    `,
  parameters: markModuleItemReadDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkModuleItemReadData, "url"> ) => {
    try {
      const { data } = await markModuleItemRead(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
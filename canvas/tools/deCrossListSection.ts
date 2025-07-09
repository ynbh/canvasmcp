
import { tool } from "ai";
import { deCrossListSectionDataSchema } from "./aitm.schema.ts";
import { deCrossListSection, DeCrossListSectionData } from "..";

export default tool({
  description: `
  De-cross-list a Section
Undo cross-listing of a Section, returning it to its original course.
    `,
  parameters: deCrossListSectionDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeCrossListSectionData, "url"> ) => {
    try {
      const { data } = await deCrossListSection(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
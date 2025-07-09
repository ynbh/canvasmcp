
import { tool } from "ai";
import { crossListSectionDataSchema } from "./aitm.schema.ts";
import { crossListSection, CrossListSectionData } from "..";

export default tool({
  description: `
  Cross-list a Section
Move the Section to another course.  The new course may be in a different
account (department),
but must belong to the same root account (institution).
    `,
  parameters: crossListSectionDataSchema.omit({ url: true }),
  execute: async (args : Omit<CrossListSectionData, "url"> ) => {
    try {
      const { data } = await crossListSection(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
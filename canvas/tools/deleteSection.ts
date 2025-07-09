
import { tool } from "ai";
import { deleteSectionDataSchema } from "./aitm.schema.ts";
import { deleteSection, DeleteSectionData } from "..";

export default tool({
  description: `
  Delete a section
Delete an existing section.  Returns the former Section.
    `,
  parameters: deleteSectionDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteSectionData, "url"> ) => {
    try {
      const { data } = await deleteSection(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { editSectionDataSchema } from "./aitm.schema.ts";
import { editSection, EditSectionData } from "..";

export default tool({
  description: `
  Edit a section
Modify an existing section.
    `,
  parameters: editSectionDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditSectionData, "url"> ) => {
    try {
      const { data } = await editSection(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
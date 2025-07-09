
import { tool } from "ai";
import { getSectionInformationSectionsDataSchema } from "./aitm.schema.ts";
import { getSectionInformationSections, GetSectionInformationSectionsData } from "..";

export default tool({
  description: `
  Get section information
Gets details about a specific section
    `,
  parameters: getSectionInformationSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSectionInformationSectionsData, "url"> ) => {
    try {
      const { data } = await getSectionInformationSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
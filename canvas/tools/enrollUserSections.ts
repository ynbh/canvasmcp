
import { tool } from "ai";
import { enrollUserSectionsDataSchema } from "./aitm.schema.ts";
import { enrollUserSections, EnrollUserSectionsData } from "..";

export default tool({
  description: `
  Enroll a user
Create a new user enrollment for a course or section.
    `,
  parameters: enrollUserSectionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<EnrollUserSectionsData, "url"> ) => {
    try {
      const { data } = await enrollUserSections(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
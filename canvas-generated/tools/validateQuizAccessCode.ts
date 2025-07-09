
import { tool } from "ai";
import { validateQuizAccessCodeDataSchema } from "./aitm.schema.ts";
import { validateQuizAccessCode, ValidateQuizAccessCodeData } from "..";

export default tool({
  description: `
  Validate quiz access code
Accepts an access code and returns a boolean indicating whether that
access code is correct
    `,
  parameters: validateQuizAccessCodeDataSchema.omit({ url: true }),
  execute: async (args : Omit<ValidateQuizAccessCodeData, "url"> ) => {
    try {
      const { data } = await validateQuizAccessCode(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
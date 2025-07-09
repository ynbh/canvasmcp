
import { tool } from "ai";
import { abortGenerationOfReportOrRemovePreviouslyGeneratedOneDataSchema } from "./aitm.schema.ts";
import { abortGenerationOfReportOrRemovePreviouslyGeneratedOne, AbortGenerationOfReportOrRemovePreviouslyGeneratedOneData } from "..";

export default tool({
  description: `
  Abort the generation of a report, or remove a previously generated one
This API allows you to cancel
a previous request you issued for a report to
be generated. Or in the case of an already generated
report, you'd like to
remove it, perhaps to generate it another time with an updated version
that
provides new features.

You must check the report's generation status before attempting to use
this
interface. See the "workflow_state" property of the QuizReport's Progress
object for more
information. Only when the progress reports itself in a
"queued" state can the generation be
aborted.

*Responses*

- <code>204 No Content</code> if your request was accepted
- <code>422
Unprocessable Entity</code> if the report is not being generated
or can not be aborted at this stage
    `,
  parameters: abortGenerationOfReportOrRemovePreviouslyGeneratedOneDataSchema.omit({ url: true }),
  execute: async (args : Omit<AbortGenerationOfReportOrRemovePreviouslyGeneratedOneData, "url"> ) => {
    try {
      const { data } = await abortGenerationOfReportOrRemovePreviouslyGeneratedOne(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
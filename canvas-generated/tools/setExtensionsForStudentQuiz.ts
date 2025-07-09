
import { tool } from "ai";
import { setExtensionsForStudentQuizDataSchema } from "./aitm.schema.ts";
import { setExtensionsForStudentQuiz, SetExtensionsForStudentQuizData } from "..";

export default tool({
  description: `
  Set extensions for student quiz submissions
<b>Responses</b>

* <b>200 OK</b> if the request was
successful
* <b>403 Forbidden</b> if you are not allowed to extend quizzes for this course
    `,
  parameters: setExtensionsForStudentQuizDataSchema.omit({ url: true }),
  execute: async (args : Omit<SetExtensionsForStudentQuizData, "url"> ) => {
    try {
      const { data } = await setExtensionsForStudentQuiz(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
// Get the number of likes by axios.
    let res

    async function getStars(id) {
        try {
            res = await axios.get('/like/' + id)

            console.log(res)
        } catch (err) {
            res = err.response
            console.log(res)

        } finally {
            target = document.getElementById("stars")
            target.innerHTML = "<p class=\"display-6\">&#x1f60d;" + res.data + " Likes</p>";

            return false;

        }
    }
